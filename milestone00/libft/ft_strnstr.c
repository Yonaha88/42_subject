/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strnstr.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/25 15:04:19 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/03 10:58:09 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strnstr(const char *big, const char *little, size_t len)
{
	size_t	idx;
	size_t	offset;
	size_t	little_len;

	little_len = ft_strlen(little);
	if (little_len == 0)
		return ((char *)big);
	idx = 0;
	while (idx < len && big[idx])
	{
		if (big[idx] == *little)
		{
			offset = 0;
			while (idx + offset < len && big[idx + offset]
				&& big[idx + offset] == little[offset])
				offset++;
			if (offset == little_len)
				return ((char *)big + idx);
		}
		idx++;
	}
	return (NULL);
}
