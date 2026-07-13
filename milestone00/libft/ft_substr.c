/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_substr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/26 16:03:18 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:20:45 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_substr(char const *s, unsigned int start, size_t len)
{
	size_t	s_len;
	size_t	sub_len;
	char	*dup;

	if (s == NULL)
		return (NULL);
	s_len = ft_strlen(s);
	if (s_len <= start)
	{
		dup = (char *)malloc(1);
		if (dup == NULL)
			return (NULL);
		dup[0] = '\0';
		return (dup);
	}
	else if (s_len - start > len)
		sub_len = len;
	else
		sub_len = s_len - start;
	dup = (char *)malloc((sub_len + 1) * sizeof(char));
	if (dup == NULL)
		return (NULL);
	ft_strlcpy(dup, s + start, sub_len + 1);
	return (dup);
}
