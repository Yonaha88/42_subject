/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strdup.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/26 15:17:11 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:29:22 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strdup(const char *src)
{
	char	*dup;
	size_t	src_len;

	src_len = ft_strlen(src);
	dup = (char *)ft_calloc(src_len + 1, sizeof(char));
	if (dup == NULL)
		return (NULL);
	ft_strlcpy(dup, src, src_len + 1);
	return (dup);
}
